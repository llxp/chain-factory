import { Checkbox, TableCell } from '@material-ui/core';
import React from 'react';

export interface ISelectAllCheckboxProps {
    selected?: boolean;
    selectable?: boolean;
    handleChange: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => void;
}

const CustomTableCell = (props) => {
  return (
    <TableCell
      style={{ backgroundColor: "#d0d0d0" }}
      align="left"
      size="small"
      {...props}
    >{props.children}</TableCell>
  );
};

export default function SelectAllCheckbox(props: ISelectAllCheckboxProps) {
  if (!props.selectable) {
    return <></>;
  }
  return <CustomTableCell padding="checkbox"><Checkbox
    checked={props.selected}
    onChange={props.handleChange}
    color="primary"
  /></CustomTableCell>;
}