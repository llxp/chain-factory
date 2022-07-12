import {
  Hidden,
  IconButton,
  TableCell,
  TableHead,
  TableRow,
} from "@material-ui/core";
import React from "react";
import SelectAllCheckbox from "./SelectAllCheckbox";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import ExpandLessIcon from '@material-ui/icons/ExpandLess';

export interface ICollapsedTableHeadProps {
  selectable?: boolean;
  selectedAll: boolean;
  expandedAll: boolean;
  handleSelectAll: (
    event: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => void;
  headerLabels: string[];
  expandAll?: () => void;
}

export default function CollapsedTableHead(props: ICollapsedTableHeadProps) {
  const { selectable, selectedAll, expandedAll, handleSelectAll, headerLabels, expandAll } = props;

  const headerCells = headerLabels.map((headerLabel) => {
    return (
      <TableCell key={headerLabel} style={{ backgroundColor: "#d0d0d0" }}>
        {headerLabel}
      </TableCell>
    );
  });

  return (<>
    <TableHead>
      <TableRow key="header">
        <SelectAllCheckbox
          selectable={selectable}
          selected={selectedAll}
          handleChange={handleSelectAll}
        />
        <TableCell style={{ backgroundColor: "#d0d0d0" }}>
          <Hidden xsDown>
            <IconButton size="small" onClick={expandAll}>
              { expandedAll ? <ExpandMoreIcon /> : <ExpandLessIcon/> }
            </IconButton>
          </Hidden>
        </TableCell>
        {headerCells}
      </TableRow>
    </TableHead>
    </>
  );
}
