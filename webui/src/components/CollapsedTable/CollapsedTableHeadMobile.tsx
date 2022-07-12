import { Hidden, TableCell } from "@material-ui/core";
import React from "react";
import RefreshButton from "./RefreshButton";
import SearchBox from "./SearchBox";
import SelectAllCheckbox from "./SelectAllCheckbox";

export default function CollapsedTableHeadMobile({ selectable, selectedAll, onSelectAll, onSearch, onRefresh }) {
  return (
    <Hidden smUp>
      <TableCell style={{ backgroundColor: "#d0d0d0", width: "100vw" }}>
        {selectable ? (
          <SelectAllCheckbox
            selected={selectedAll}
            handleChange={onSelectAll}
          />
        ) : (
          <></>
        )}
        <SearchBox style={{ width: "70%" }} onSearch={onSearch}/>
        <RefreshButton onRefresh={onRefresh}/>
      </TableCell>
    </Hidden>
  );
}
