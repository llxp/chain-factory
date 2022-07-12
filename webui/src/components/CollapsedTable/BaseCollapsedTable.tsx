import { TableContainer, Table, Theme } from "@material-ui/core";
import React, { useRef, useState } from "react";
import { ICollapsedTableRowProps } from "./CollapsedTableRow";
import { isMobile } from "react-device-detect";
import CollapsedTableBody from "./CollapsedTableBody";
import CollapsedTableHead from "./CollapsedTableHead";
import { getWindowDimensions } from "../../utils/ScreenUtils";
import { makeStyles } from "@material-ui/styles";

const heightMobile = getWindowDimensions().height - 190;
const heightDesktop = 550; //getWindowDimensions().height - 250;

const useStyles = makeStyles((theme: Theme) => ({
  table: {
    minWidth: '100%',
    maxHeight: isMobile ? heightMobile : heightDesktop,
    minHeight: isMobile ? heightMobile : heightDesktop,
  },
  pagination: {
    backgroundColor: theme.palette.background.paper,
  }
}));


export interface IBaseCollapsedTableProps {
  rows?: ICollapsedTableRowProps[];
  headerLabels: string[];
  rowColumnOrder?: string[];
  selectable?: boolean;
  expandedRows?: string[];
  setExpandedRows?: (expandedRows: string[]) => void;
  selectedRows?: string[];
  setSelectedRows?: (selectedRows: string[]) => void;
}

export default function BaseCollapsedTable(props: IBaseCollapsedTableProps) {
  const { rows, headerLabels, selectable, rowColumnOrder, expandedRows, setExpandedRows, selectedRows, setSelectedRows } = props;
  const [selectedAll, setSelectedAll] = useState(false);
  const [expandedAll, setExpandedAll] = useState(true);
  const classes = useStyles();
  const anchorEl = useRef<null | HTMLTableElement>(null);

  const isSelected = (name: string) => (selectedRows || []).indexOf(name) !== -1;
  const isExpanded = (name: string) => (expandedRows || []).indexOf(name) !== -1;

  const handleSelectAll = (
    event: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => {
    setSelectedAll(checked);
    if (checked && rows) {
      setSelectedRows?.(
        rows.map((row) => {
          return row.key;
        })
      );
      return;
    }
    setSelectedRows?.([]);
  };

  const handleExpandedAll = (
  ) => {
    setExpandedAll(!expandedAll);
    if (expandedAll && rows) {
      setExpandedRows?.(
        rows.map((row) => {
          return row.key;
        })
      );
      return;
    }
    setExpandedRows?.([]);
  };

  return (<TableContainer className={classes.table} ref={anchorEl}>
    <Table aria-label="collapsible table" stickyHeader>
      <CollapsedTableHead
        selectable={selectable}
        selectedAll={selectedAll}
        handleSelectAll={handleSelectAll}
        headerLabels={headerLabels}
        expandedAll={expandedAll}
        expandAll={handleExpandedAll}
      />
      <CollapsedTableBody
        rows={rows || []}
        selectable={selectable}
        selectedRows={selectedRows || []}
        expandedRows={expandedRows || []}
        setSelectedRows={setSelectedRows || (() => { })}
        setExpandedRows={setExpandedRows || (() => { })}
        isSelected={isSelected}
        isExpanded={isExpanded}
        rowColumnOrder={rowColumnOrder}
      />
    </Table>
  </TableContainer>);
}
