from .imusic_player import IMusicPlayer, MAX_SEARCH_RESULTS
from .music_player_worker import MusicPlayerWorker
from .enums import QueueMode
from .models import MusicContext, Song
from datetime import datetime, timedelta
from holobot.discord.sdk.audio import IAudioClient, IAudioSourceFactory
from holobot.discord.sdk.audio.events import UserJoinedAudioChannelEvent, UserLeftAudioChannelEvent
from holobot.discord.sdk.audio.models import SongMetadata
from holobot.discord.sdk.models import PagedResults
from holobot.discord.sdk.servers import IVoiceChannelConnectionFactory
from holobot.discord.sdk.servers.managers import IChannelManager
from holobot.sdk.caching import ConcurrentCache
from holobot.sdk.concurrency import AsyncProducerConsumerQueue, CancellationToken
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.lifecycle import StartableInterface
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from holobot.sdk.utils import assert_not_none, assert_range, take
from typing import Any, Generator, List, Optional, Tuple, Union

import asyncio, math, sys

class WorkerDisposer:
    def __init__(self) -> None:
        self.__disposable_workers: AsyncProducerConsumerQueue[MusicPlayerWorker] = AsyncProducerConsumerQueue()
        self.__token: CancellationToken = CancellationToken()
        self.__consumer: Optional[asyncio.Task] = None
    
    async def add(self, worker: MusicPlayerWorker) -> None:
        assert_not_none(worker, "worker")
        await self.__disposable_workers.enqueue(worker)

    def start(self) -> None:
        if self.__consumer:
            raise InvalidOperationError("The consumer has been started already.")
        self.__consumer = asyncio.create_task(self.__dispose_continuously(self.__token))

    async def stop(self) -> None:
        await self.__disposable_workers.complete()
        self.__token.cancel()

    def __await__(self) -> Generator[Any, None, None]:
        if not self.__consumer:
            return
        yield from self.__consumer.__await__()
    
    async def __dispose_continuously(self, token: CancellationToken) -> None:
        await asyncio.sleep(0) # Yield
        while True:
            try:
                worker = await self.__disposable_workers.try_dequeue()
            except InvalidOperationError:
                break

            if worker.has_value:
                await worker.value
                continue
            if token.is_cancellation_requested:
                break
            await asyncio.sleep(10)

@injectable(ListenerInterface[UserLeftAudioChannelEvent])
@injectable(ListenerInterface[UserJoinedAudioChannelEvent])
@injectable(StartableInterface)
@injectable(IMusicPlayer)
class MusicPlayer(IMusicPlayer, StartableInterface, ListenerInterface[Any]):
    def __init__(self,
                 audio_source_factory: IAudioSourceFactory,
                 channel_manager: IChannelManager,
                 configurator: ConfiguratorInterface,
                 log: LogInterface,
                 voice_channel_connection_factory: IVoiceChannelConnectionFactory) -> None:
        super().__init__()
        self.__audio_source_factory: IAudioSourceFactory = audio_source_factory
        self.__channel_manager: IChannelManager = channel_manager
        self.__log: LogInterface = log.with_name("Music", "MusicPlayer")
        self.__voice_channel_connection_factory: IVoiceChannelConnectionFactory = voice_channel_connection_factory
        self.__queue_size_max: int = configurator.get("Music", "QueueSizeMax", 50)
        self.__workers: ConcurrentCache[str, MusicPlayerWorker] = ConcurrentCache()
        self.__disposer: WorkerDisposer = WorkerDisposer()

    async def start(self):
        self.__disposer.start()

    async def stop(self):
        for worker in await self.__workers.get_all():
            await self.__disconnect(worker)
            await worker
        await self.__disposer.stop()
        await self.__disposer
    
    async def join_channel(self, server_id: str, channel_id: str, initiating_user_id: str) -> None:
        assert_not_none(server_id, "server_id")
        assert_not_none(channel_id, "channel_id")
        assert_not_none(initiating_user_id, "initiating_user_id")

        worker = await self.__workers.get_or_add(server_id, lambda sid: self.__create_worker(sid, channel_id, initiating_user_id))
        if worker.music_context.channel_id != channel_id:
            raise InvalidOperationError("The bot is playing music in another channel already.")

    async def stop_playback(self, server_id: str, clear_queue: bool, leave_channel: bool) -> None:
        assert_not_none(server_id, "server_id")

        worker = await self.__workers.get(server_id)
        if not worker:
            raise InvalidOperationError("The bot isn't connected to a voice channel.")

        await worker.stop_playback()
        if leave_channel:
            await self.__disconnect(worker)
            await worker
            return
        
        if clear_queue:
            await worker.music_context.queue.clear()
            worker.music_context.current_song = None

    async def queue_songs(self, server_id: str, user_id: str, url: str, mode: QueueMode = QueueMode.AS_LAST) -> Tuple[Song, ...]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(url, "url")

        worker = await self.__workers.get(server_id)
        if not worker:
            raise InvalidOperationError("The bot isn't connected to a voice channel.")
        
        playlist_items = await self.__audio_source_factory.create_from_url(url)
        if mode != QueueMode.AS_LAST:
            playlist_items = reversed(playlist_items)

        queued_songs: List[Song] = []
        for playlist_item in take(playlist_items, self.__queue_size_max - len(worker.music_context.queue)):
            song = Song(
                url=url,
                queueing_user_id=user_id,
                audio_source=playlist_item
            )
            queued_songs.append(song)
            if mode == QueueMode.AS_LAST:
                await worker.music_context.queue.enqueue(song)
            else: await worker.music_context.queue.enqueue(song, 0)

        if mode == QueueMode.SKIP_CURRENT:
            await worker.skip_song()
        
        return tuple(queued_songs)
    
    async def skip_song(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        worker = await self.__workers.get(server_id)
        if not worker:
            raise InvalidOperationError("The bot isn't connected to a voice channel.")
        await worker.skip_song()

    async def search_songs(self, keywords: str, max_count: int = MAX_SEARCH_RESULTS) -> Tuple[SongMetadata, ...]:
        assert_not_none(keywords, "keywords")
        return await self.__audio_source_factory.search(keywords, max_count)

    async def get_channel_id(self, server_id: str) -> Optional[str]:
        assert_not_none(server_id, "server_id")

        worker = await self.__workers.get(server_id)
        return worker.music_context.channel_id if worker else None
    
    async def get_currently_playing_song(self, server_id: str) -> Optional[Song]:
        assert_not_none(server_id, "server_id")

        worker = await self.__workers.get(server_id)
        return worker.music_context.current_song if worker else None
    
    async def get_queued_songs(self, server_id: str, page_index: int, page_size: int = 10) -> PagedResults[Song]:
        assert_not_none(server_id, "server_id")
        assert_range(page_index, 0, sys.maxsize, "page_index")
        assert_range(page_size, 1, 10, "page_size")
        
        worker = await self.__workers.get(server_id)
        if not worker:
            return PagedResults(tuple(), 0, 0, 0)
        
        queue = worker.music_context.queue
        start_offset = page_index * page_size
        end_offset = start_offset + min(len(queue) - start_offset, page_size)
        return PagedResults(
            results=tuple(await queue.peek(slice(start_offset, end_offset))),
            page_index=page_index,
            page_count=math.ceil(len(queue) / float(page_size)),
            total_results=len(queue)
        )

    async def on_event(self, event: Union[UserLeftAudioChannelEvent, UserJoinedAudioChannelEvent]) -> None:
        if isinstance(event, UserJoinedAudioChannelEvent):
            self.__log.debug(f"User joined a voice channel. {{ ServerId = {event.server_id}, ChannelId = {event.channel_id}, UserId = {event.user_id} }}")
            return

        if isinstance(event, UserLeftAudioChannelEvent):
            self.__log.debug(f"User left a voice channel. {{ ServerId = {event.server_id}, ChannelId = {event.channel_id}, UserId = {event.user_id} }}")
            if not event.server_id or not event.channel_id:
                return
            await self.__disconnect_if_alone(event.server_id, event.channel_id)

    async def __create_worker(self, server_id: str, channel_id: str, initiating_user_id: str) -> MusicPlayerWorker:
        return MusicPlayerWorker(
            MusicContext(
                server_id,
                channel_id,
                initiating_user_id),
            await self.__voice_channel_connection_factory.create(server_id, channel_id),
            CancellationToken(),
            self.__try_disconnect
        )
    
    async def __disconnect(self, worker: MusicPlayerWorker) -> None:
        worker.shutdown()
        # Not awaiting here to avoid blocking an executing command.
        # await worker
        await worker.audio_client.close()
        await self.__workers.remove(worker.music_context.server_id)

    async def __try_disconnect(self, worker: MusicPlayerWorker) -> None:
        if datetime.utcnow() - worker.music_context.last_song_finished_at < timedelta(minutes=5):
            return
        await self.__disconnect(worker)
        await self.__disposer.add(worker)

    async def __disconnect_if_alone(self, server_id: str, channel_id: str) -> None:
        if (not (channel := self.__channel_manager.get_audio_channel(server_id, channel_id))
            or len(channel.member_ids) > 1
            or not (worker := await self.__workers.get(server_id))):
            return

        await self.__disconnect(worker)
        await self.__disposer.add(worker)
