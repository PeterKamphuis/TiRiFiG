"""Service for updating the graph grid row/column layout."""


class SetRowColService:
    """Encapsulate MainWindow.setRowCol behavior with unchanged flow."""

    @staticmethod
    def set_row_col(owner, qt_widgets, message_box_cls):
        """Prompt for rows/columns and relayout graph widgets."""
        text, ok = qt_widgets.QInputDialog.getText(
            owner,
            "Window number Input Dialog",
            "Specify the number of rows and columns (rows,columns):",
        )
        if not ok:
            return

        if text:
            text = str(text)
            text = text.split(",")
            owner.nrows = int(float(text[0]))
            owner.ncols = int(float(text[1]))
            if (owner.nrows * owner.ncols) >= len(owner.par):
                item_count = owner.scroll_grid_layout.count()
                for _ in range(item_count):
                    widget_to_remove = owner.scroll_grid_layout.itemAt(0).widget()
                    owner.scroll_grid_layout.removeWidget(widget_to_remove)
                    widget_to_remove.close()

                g_w_to_plot = [
                    gw_object for gw_object in owner.gwObjects if gw_object.par in owner.par
                ]
                g_w_pars = [g_w.par for g_w in g_w_to_plot]
                sorted_g_w_to_plot = []
                for par in owner.par:
                    idx = g_w_pars.index(par)
                    sorted_g_w_to_plot.append(g_w_to_plot[idx])
                del g_w_to_plot

                counter = 0
                for col in range(owner.ncols):
                    for row in range(owner.nrows):
                        owner.scroll_grid_layout.addWidget(
                            sorted_g_w_to_plot[counter], row, col
                        )
                        sorted_g_w_to_plot[counter].show()
                        if counter == len(sorted_g_w_to_plot) - 1:
                            break
                        counter += 1
                for col in range(owner.ncols):
                    owner.scroll_grid_layout.setColumnStretch(col, 1)
                    owner.scroll_grid_layout.setColumnMinimumWidth(col, 0)
                for row in range(owner.nrows):
                    owner.scroll_grid_layout.setRowStretch(row, 1)
                del sorted_g_w_to_plot
            else:
                message_box_cls.information(
                    owner,
                    "Information",
                    "Product of rows and columns should"
                    " be at least the same as the current number of parameters"
                    " on viewgraph",
                )
