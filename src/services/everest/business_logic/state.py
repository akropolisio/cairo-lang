import contextlib
from abc import ABC, abstractmethod
from typing import Generic, Iterator, Optional, Type, TypeVar

from starkware.python.object_utils import generic_object_repr
from starkware.starkware_utils.commitment_tree.binary_fact_tree import BinaryFactDict
from starkware.starkware_utils.config_base import Config
from starkware.storage.storage import FactFetchingContext

TStateSelector = TypeVar("TStateSelector", bound="StateSelectorBase")
TCarriedState = TypeVar("TCarriedState", bound="CarriedStateBase")
TSharedState = TypeVar("TSharedState", bound="SharedStateBase")
TGeneralConfig = TypeVar("TGeneralConfig", bound=Config)


class StateSelectorBase(ABC):
    """
    A class that contains a set of leaf IDs for each Merkle tree in the SharedState objects.
    It is used to fetch a subset of the leaves relevant to a chunk of transactions that is being
    processed.
    """

    @classmethod
    @abstractmethod
    def empty(cls: Type[TStateSelector]) -> TStateSelector:
        pass

    def __repr__(self) -> str:
        return generic_object_repr(obj=self)

    @abstractmethod
    def __and__(self: TStateSelector, other: TStateSelector) -> TStateSelector:
        pass

    @abstractmethod
    def __or__(self: TStateSelector, other: TStateSelector) -> TStateSelector:
        pass

    @abstractmethod
    def __sub__(self: TStateSelector, other: TStateSelector) -> TStateSelector:
        pass

    @abstractmethod
    def __le__(self: TStateSelector, other: TStateSelector) -> bool:
        pass


class CarriedStateBase(Generic[TCarriedState], ABC):
    """
    A class representing a sub-state of the total state (SharedState).
    It is carried and maintained by the Batcher, as each pending transaction is applied to it
    during the attempt to include it in a batch.
    After a batch is created the carried state is applied to the shared state.

    If self.parent_state is not None, it acts as a view object object of its parent.
    This is used both for idempotent update of CarriedState and as a light-weight copy of
    information of the (usually) larger parent state.

    CarriedState absorbs all transaction-induced changes and only if they are all legal -
    they are applied to the parent CarriedState object.
    Note that this is the intended use and is not enforced by this class.
    """

    def __init__(self, parent_state: Optional[TCarriedState]):
        """
        Private constructor.
        Should only be called by _create_from_parent_state and create_unfilled class methods.
        """
        self.parent_state = parent_state

    def __repr__(self) -> str:
        return generic_object_repr(obj=self)

    @classmethod
    @abstractmethod
    def _create_from_parent_state(cls, parent_state: TCarriedState) -> TCarriedState:
        """
        Instantiates a CarriedState object that acts as proxy to given parent_state.
        """

    @property
    @abstractmethod
    def state_selector(self) -> StateSelectorBase:
        """
        Returns the state selector of this CarriedState containing the IDs of the Merkle
        state leaves.
        """

    @abstractmethod
    def select(self, state_selector: StateSelectorBase) -> TCarriedState:
        """
        Returns a new CarriedState copied from this one after deleting unused Merkle state leaves.
        """

    def fill_missing(self, other: TCarriedState):
        """
        Fills missing entries from another CarriedState instance.
        """
        state_selector = self.state_selector
        assert (
            state_selector & other.state_selector == type(state_selector).empty()
        ), "Selectors must be disjoint."
        self._fill_missing(other=other)

    @abstractmethod
    def _fill_missing(self, other: TCarriedState):
        """
        Updates this state with the missing entries from another CarriedState instance.
        This is a private method, only to be called from public fill_missing method.
        """

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def subtract_merkle_facts(self, previous_state: TCarriedState) -> TCarriedState:
        """
        Returns a new object containing the subtraction of Merkle facts in previous_state from the
        ones in self. All other members of the returned object are taken from self.
        """

    def _copy(self: TCarriedState) -> TCarriedState:
        """
        Creates a lazy copy of self (pointing to self as the parent state).
        This method should not be directly used; use copy_and_apply instead.
        """
        return type(self)._create_from_parent_state(parent_state=self)

    @abstractmethod
    def _apply(self):
        """
        Applies state updates to self.parent_state.
        This method should not be directly used; use copy_and_apply instead.
        """

    @contextlib.contextmanager
    def copy_and_apply(self) -> Iterator[TCarriedState]:
        copied_state = self._copy()
        # The exit logic will not be called in case an exception is raised inside the context.
        yield copied_state
        copied_state._apply()  # Apply to self.


class SharedStateBase(ABC):
    """
    A class representing a combination of the onchain and offchain state.
    """

    def __repr__(self) -> str:
        return generic_object_repr(obj=self)

    @classmethod
    @abstractmethod
    async def empty(
        cls: Type[TSharedState], ffc: FactFetchingContext, general_config: Config
    ) -> TSharedState:
        """
        Returns an empty state. This is called before creating very first batch.
        """

    @abstractmethod
    def to_carried_state(self: TSharedState, ffc: FactFetchingContext) -> CarriedStateBase:
        """
        Returns an unfilled CarriedState.
        """

    @abstractmethod
    async def get_filled_carried_state(
        self: TSharedState, ffc: FactFetchingContext, state_selector: StateSelectorBase
    ) -> CarriedStateBase:
        pass

    @abstractmethod
    async def apply_state_updates(
        self: TSharedState,
        ffc: FactFetchingContext,
        previous_carried_state: CarriedStateBase,
        current_carried_state: CarriedStateBase,
        facts: Optional[BinaryFactDict] = None,
    ) -> TSharedState:
        pass
