"""[Layer: Use Cases] Hartley violin (HartleyViolinUseCase + HartleyUseCase 구현)."""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_use_case import HartleyUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort


class HartleyViolinInteractor(HartleyViolinUseCase, HartleyUseCase):
    def __init__(self, repository: HartleyViolinPort) -> None:
        self.repository = repository

    def correlation_graph(self, train_df: pd.DataFrame) -> bytes:
        corr = train_df.select_dtypes(include="number").corr()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
        ax.set_title("Titanic Feature Correlation with Survived")
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        return await self.repository.introduce_myself(HartleyViolinQuery(
            id=schema.id,
            name=schema.name,
        ))
