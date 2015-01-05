from .deps import (
    find_item,
    prepare_dependencies,
    remove_item_dependents,
    remove_dep_from_items,
    split_items_without_deps,
)
from .exceptions import NoSuchItem
from .utils import LOG
from .utils.text import mark_for_translation as _


class ItemQueue(object):
    def __init__(self, items):
        self.items_with_deps = prepare_dependencies(items)
        self.items_without_deps = []
        self._split()
        self.pending_items = []

    @property
    def all_items(self):
        return self.items_with_deps + self.items_without_deps

    def item_fixed(self, item):
        """
        Called when an item has successfully been fixed.
        """
        self.item_ok(item)
        self._fire_triggers_for_item(item)

    def item_ok(self, item):
        """
        Called when an item didn't need to be fixed.
        """
        self.pending_items.remove(item)
        # if an item is applied successfully, all dependencies on it can
        # be removed from the remaining items
        self.items_with_deps = remove_dep_from_items(
            self.items_with_deps,
            item.id,
        )
        self._split()

    def item_skipped(self, item):
        """
        Called when an item has been skipped. Yields all items that have
        been skipped as a result by cascading.
        """
        self.pending_items.remove(item)
        if item.cascade_skip:
            # if an item fails or is skipped, all items that depend on
            # it shall be removed from the queue
            self.items_with_deps, skipped_items = remove_item_dependents(
                self.items_with_deps,
                item.id,
            )
            # since we removed them from further processing, we
            # fake the status of the removed items so they still
            # show up in the result statistics
            for skipped_item in skipped_items:
                if skipped_item.ITEM_TYPE_NAME == 'dummy':
                    continue
                yield skipped_item

    def pop(self):
        item = self.items_without_deps.pop()
        self.pending_items.append(item)
        return item

    def _fire_triggers_for_item(self, item):
        for triggered_item_id in item.triggers:
            try:
                triggered_item = find_item(
                    triggered_item_id,
                    self.all_items,
                )
                triggered_item.has_been_triggered = True
            except NoSuchItem:
                LOG.debug(_(
                    "{item} tried to trigger {triggered_item}, "
                    "but it wasn't available. It must have been skipped previously."
                ).format(
                    item=item.id,
                    triggered_item=triggered_item_id,
                ))

    def _split(self):
        self.items_with_deps, self.items_without_deps = \
            split_items_without_deps(self.all_items)
