import json
from typing import Any, cast

import aiogoogle
import aiogoogle.auth.creds as aiogoogle_creds

from holobot.extensions.google.exceptions import QuotaExhaustedError
from holobot.extensions.google.models import GoogleClientOptions, Language, Translation
from holobot.sdk import AsyncLazy
from holobot.sdk.configs import IOptions
from holobot.sdk.exceptions import ArgumentError, InvalidOperationError
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience import AsyncCircuitBreakerPolicy
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError
from holobot.sdk.serialization.json_serializer import deserialize
from .dtos.languages_response import LanguagesResult
from .dtos.translation_response import TranslationResult

class TranslationEndpoint:
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        options: IOptions[GoogleClientOptions]
    ) -> None:
        self.__log = logger_factory.create(TranslationEndpoint)
        self.__options = options
        self.__endpoint = AsyncLazy(self.__get_endpoint)
        self.__languages = AsyncLazy(self.__get_languages)
        self.__circuit_breaker = AsyncCircuitBreakerPolicy[Any, Translation | None](
            options.value.CircuitBreakerFailureThreshold,
            options.value.CircuitBreakerRecoveryTime,
            TranslationEndpoint.__on_circuit_broken
        )

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None
    ) -> Translation | None:
        if not await self.__endpoint.get_value():
            raise InvalidOperationError("Google translations aren't configured.")
        if not text:
            raise ArgumentError("text", "The text to be translated must be specified.")
        if not target_language:
            raise ArgumentError("target_language", "The target language must be specified.")

        target_language = target_language.lower()
        languages = await self.__languages.get_value()
        if target_language not in languages:
            raise ArgumentError("target_language", "This language is not supported.")
        if source_language:
            source_language = source_language.lower()
            if source_language not in languages:
                raise ArgumentError("source_language", "This language is not supported.")

        try:
            return await self.__circuit_breaker.execute(
                lambda _: self.__translate_text(
                    text,
                    target_language,
                    source_language
                ),
                0
            )
        except TooManyRequestsError as error:
            raise QuotaExhaustedError from error
        except HttpStatusError as error:
            self.__log.error("An HTTP error has occurred during a Google translation request", error)
            raise
        except CircuitBrokenError:
            raise
        except Exception as error:
            self.__log.error("An unexpected error has occurred during a Google translation request", error)
            raise

    async def get_languages(self) -> dict[str, Language]:
        return await self.__languages.get_value()

    async def get_language_by_code(self, code: str) -> Language | None:
        languages = await self.__languages.get_value()
        return languages.get(code)

    @staticmethod
    async def __on_circuit_broken(
        circuit_breaker: AsyncCircuitBreakerPolicy[tuple[dict[str, Any], dict[str, Any]], Any],
        error: Exception
    ) -> int:
        if (isinstance(error, TooManyRequestsError)
            and error.retry_after is not None
            and isinstance(error.retry_after, int)):
            return error.retry_after
        return circuit_breaker.recovery_timeout

    async def __get_endpoint(
        self
    ) -> tuple[aiogoogle.Aiogoogle, aiogoogle.GoogleAPI] | None:
        if not self.__options.value.ServiceAccountCredentialFile:
            return None

        service_account_key = json.load(open(self.__options.value.ServiceAccountCredentialFile))
        creds = aiogoogle_creds.ServiceAccountCreds(
            scopes=[
                "https://www.googleapis.com/auth/cloud-translation",
                "https://www.googleapis.com/auth/cloud-platform"
            ],
            **service_account_key
        )
        client = aiogoogle.Aiogoogle(service_account_creds=creds)
        async with client:
            return (client, await client.discover("translate", "v2"))

    async def __get_languages(self) -> dict[str, Language]:
        endpoint = await self.__endpoint.get_value()
        if not endpoint:
            return {}

        client, api = endpoint

        async with client:
            response = await client.as_service_account(
                # Ignored type, because it's a dynamically generated method.
                api.languages.list(target="en")  # type: ignore
            )
            result = deserialize(LanguagesResult, cast(dict, response))
            if not result or not result.data or not result.data.languages:
                return {}

            return {
                language.language: Language(code=language.language, name=language.name)
                for language in result.data.languages
            }

    async def __translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None
    ) -> Translation | None:
        endpoint = await self.__endpoint.get_value()

        # The calling public method must ensure there is a client.
        assert endpoint
        client, api = endpoint

        request_data = {
            "format": "text",
            "q": text,
            "target": target_language
        }
        if source_language:
            request_data["source"] = source_language

        async with client:
            response = await client.as_service_account(api.translations.list(**request_data))
            result = deserialize(TranslationResult, cast(dict, response))
            if not result or not result.data.translations:
                return None

            return Translation(
                source_text=text,
                source_language=(
                    source_language or result.data.translations[0].detectedSourceLanguage or "??"
                ),
                result_text=result.data.translations[0].translatedText,
                result_language=target_language
            )
