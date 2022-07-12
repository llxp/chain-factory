import { Box, Collapse, IconButton, TableCell, TableRow } from "@material-ui/core";
import { makeStyles } from '@material-ui/styles';
import KeyboardArrowUpIcon from "@material-ui/icons/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@material-ui/icons/KeyboardArrowDown";
import React from "react";
import SelectAllCheckbox from "./SelectAllCheckbox";

export interface IPCollapsedTableRowProps extends ICollapsedTableRowProps {
  handleSelected: (
    event: React.ChangeEvent<HTMLInputElement>,
    checked: boolean
  ) => void;
  selected: boolean;
  expanded: boolean;
  onExpand: (
    expanded: boolean
  ) => void;
  rowColumnOrder?: string[];
}

export interface ICollapsedTableRowProps {
  firstKey: string;
  key: string;
  row: Object;
  rowComponent?: JSX.Element;
  selectable?: boolean;
}

const useRowStyles = makeStyles({
  root: {
    "& > *": {
      borderBottom: "unset",
    },
  },
  secondTableRow: {
    paddingBottom: 0,
    paddingTop: 0,
  },
});

export default function CollapsedTableRow(props: IPCollapsedTableRowProps) {
  const { row, selectable, selected, firstKey, handleSelected, rowComponent, rowColumnOrder, expanded, onExpand } = props;
  //const [open, setOpen] = useState(false);
  const classes = useRowStyles();
  let keys = Object.keys(row);

  const onClick = (e) => {
    onExpand(!expanded);
  };

  const expandButton = (
    <TableCell onClick={onClick}>
      <IconButton aria-label="expand row" size="small">
        {expanded ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
      </IconButton>
    </TableCell>
  );

  const checkBox = <SelectAllCheckbox selectable={selectable} handleChange={handleSelected} selected={selected} />;

  const firstRowCell = (key: string) => {
    const scope = {};
    if (key === firstKey) {
      scope['scope'] = 'row';
      scope['component'] = 'th';
    } else {
      scope['component'] = 'td';
    }
    return (
      <TableCell onClick={onClick} key={key + row[key]} {...scope}>
        {row[key]}
      </TableCell>
    );
  };

  const firstRow = (
    <TableRow key={row[firstKey] + "12"} className={classes.root}>
      {checkBox}
      {expandButton}
      {
        (rowColumnOrder || keys).map((key) => {
          return firstRowCell(key);
        })
      }
    </TableRow>
  );

  const secondRow = rowComponent ? (
    <TableRow key={row[firstKey] + "2"}>
      <TableCell className={classes.secondTableRow} colSpan={(rowColumnOrder || keys).length + 2}>
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box margin={1}>{rowComponent}</Box>
        </Collapse>
      </TableCell>
    </TableRow>
  ) : (
    <></>
  );

  return (
    <React.Fragment>
      {firstRow}
      {secondRow}
    </React.Fragment>
  );
}
