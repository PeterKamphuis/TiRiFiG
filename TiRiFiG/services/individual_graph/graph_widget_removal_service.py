"""Helpers for removing displayed graph widgets from the main grid."""


class GraphWidgetRemovalService:
    """Encapsulate MainWindow graph-widget removal behavior."""

    @staticmethod
    def _compact_layout(owner):
        """Repack displayed widgets to eliminate empty grid gaps."""
        positioned_widgets = []
        for i in range(owner.scroll_grid_layout.count()):
            displayed = owner.scroll_grid_layout.itemAt(i).widget()
            row_number, column_number = owner.get_widget_location(displayed)
            positioned_widgets.append((column_number, row_number, displayed))

        positioned_widgets.sort(key=lambda item: (item[0], item[1]))

        for i in range(owner.scroll_grid_layout.count() - 1, -1, -1):
            widget_to_remove = owner.scroll_grid_layout.itemAt(i).widget()
            owner.scroll_grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.hide()

        owner.par = []
        nrows = max(1, int(owner.nrows))
        for idx, (_col, _row, widget) in enumerate(positioned_widgets):
            new_row = idx % nrows
            new_col = idx // nrows
            owner.scroll_grid_layout.addWidget(widget, new_row, new_col)
            widget.show()
            owner.par.append(widget.par)

    @staticmethod
    def remove_current_parameter_widget(owner, current_parameter):
        """Remove the widget for the current parameter and keep state in sync."""
        print(f"Removing the Graph of parameter {current_parameter}")
        widgets = [owner.scroll_grid_layout.itemAt(i).widget() for i in range(owner.scroll_grid_layout.count())]
        widget_to_remove = next((widget for widget in widgets if widget.par == current_parameter), None)
        if widget_to_remove is None:
            return

        owner.scroll_grid_layout.removeWidget(widget_to_remove)

        # Do not keep removed widgets in cache: re-adding should create a fresh widget.
        owner.gwObjects = [gw for gw in owner.gwObjects if gw is not widget_to_remove]
        GraphWidgetRemovalService._compact_layout(owner)
        owner.scroll_grid_layout.update()
        widget_to_remove.deleteLater()
