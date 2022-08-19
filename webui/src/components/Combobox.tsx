import React from "react";
import Autocomplete, { AutocompleteChangeDetails, AutocompleteChangeReason, AutocompleteRenderInputParams } from '@material-ui/lab/Autocomplete';
import TextField from "@material-ui/core/TextField";
import { makeStyles } from "@material-ui/core";

export interface IComboboxItem {
  display: string;
  value?: string;
  group?: string;
}

export interface IComboboxProps {
  options: IComboboxItem[];
  handleChange?: { (event: React.ChangeEvent<{}>, value: any, reason: AutocompleteChangeReason, details?: AutocompleteChangeDetails<any> | undefined): void };
  label: string;
  currentOption?: IComboboxItem;
}

export default function Combobox(props: IComboboxProps) {
  const { options, handleChange, label, currentOption } = props;
  const defaultOption: IComboboxItem = {
    display: 'default',
    value: 'default',
  };
  const autocompleteStyles = makeStyles({
    root: {
      width: 200,
    },
    textField: {
      color: "#ffffff",
      "& label.Mui-focused": {
        color: "#000000",
        borderColor: "#00000088",
        borderWidth: "1px",
      },
      "& .MuiOutlinedInput-root": {
        "& fieldset": {
          borderColor: "#00000055",
          borderWidth: "1px",
        },
        "&.Mui-focused fieldset": {
          borderColor: "#000000ff",
          borderWidth: "1px",
        },
      },
      "& .MuiOutlinedInput-root:hover fieldset": {
        borderColor: "#00000088",
        borderWidth: "1px",
      },
    }
  });
  const classes = autocompleteStyles();
  const defaultOptions: IComboboxItem[] = [defaultOption, ...options];
  return (
    <Autocomplete
      options={defaultOptions}
      getOptionLabel={(option) => option.display || 'default'}
      renderInput={(params: AutocompleteRenderInputParams) => <TextField fullWidth color="primary" InputProps={params.InputProps} inputProps={params.inputProps} label={label} variant="outlined" size="small" className={classes.textField}/>}
      className={classes.root}
      defaultValue={currentOption || defaultOption}
      onChange={handleChange}
      groupBy={(option) => option.group || ''}
      disableClearable
      autoHighlight
      autoSelect
      value={currentOption || defaultOption}
      inputValue={currentOption?.display || "default"}
    />
  );
}