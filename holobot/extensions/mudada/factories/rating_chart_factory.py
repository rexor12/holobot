import base64

from holobot.extensions.mudada.configs import MudadaOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.ioc import injectable
from holobot.sdk.serialization import JsonSerializer
from .irating_chart_factory import ChartData, IRatingChartFactory

_SERIALIZER = JsonSerializer()

@injectable(IRatingChartFactory)
class RatingChartFactory(IRatingChartFactory):
    def __init__(
        self,
        options: IOptions[MudadaOptions]
    ) -> None:
        super().__init__()
        self.__options = options

    def get_chart_url(
        self,
        user_name: str,
        color: str | None,
        data: ChartData
    ) -> str:
        chart_data = _SERIALIZER.serialize({
            "user": user_name,
            "color": color,
            "data": {
                "Humor": data.score1,
                "Positivity": data.score2,
                "Trust": data.score3,
                "Lewdness": data.score4,
                "Creativity": data.score5,
                "Chemistry": data.score6
            }
        })
        chart_data_b64 = str(base64.b64encode(bytes(chart_data, "utf8")), "utf8")

        return self.__options.value.RatingChartApiUrl.format(
            chart_data=chart_data_b64
        )
