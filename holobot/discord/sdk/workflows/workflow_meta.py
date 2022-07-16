from abc import ABCMeta

from .constants import DECORATOR_METADATA_NAME, WORKFLOW_PREDEFINED_INTERACTABLES

class WorkflowMeta(ABCMeta):
    def __new__(cls, name, bases, attrs, *args, **kwargs):
        attrs[WORKFLOW_PREDEFINED_INTERACTABLES] = decorator_interactables = []
        for base in bases:
            decorator_interactables.extend(getattr(base, WORKFLOW_PREDEFINED_INTERACTABLES, ()))

        for name, member in attrs.items():
            if workflow_metadata := getattr(member, DECORATOR_METADATA_NAME, None):
                decorator_interactables.append(workflow_metadata)

        return super().__new__(cls, name, bases, attrs, *args, **kwargs)
