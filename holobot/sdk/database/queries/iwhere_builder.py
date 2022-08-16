from .constraints import IConstraintBuilder
from .iquery_part_builder import IQueryPartBuilder

class IWhereBuilder(IQueryPartBuilder):
    @property
    def constraint(self) -> IConstraintBuilder:
        return self.__constraint
    
    @constraint.setter
    def constraint(self, value: IConstraintBuilder) -> None:
        self.__constraint = value
