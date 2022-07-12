import React from "react";
import Autocomplete, { AutocompleteChangeDetails, AutocompleteChangeReason } from '@material-ui/lab/Autocomplete';
import TextField from "@material-ui/core/TextField";

export interface IComboboxProps {
  options: string[];
  handleChange?: { (event: React.ChangeEvent<{}>, value: any, reason: AutocompleteChangeReason, details?: AutocompleteChangeDetails<any> | undefined): void };
  label: string;
  currentOption?: string;
}

export default function Combobox(props: IComboboxProps) {
  const {options, handleChange, label, currentOption} = props;
  const defaultOptions = ['default', ...options];
  return (
    <Autocomplete
      options={defaultOptions}
      getOptionLabel={(option) => option}
      style={{ width: 300 }}
      renderInput={(params) => <TextField {...params} label={label} variant="outlined" size="small"/>}
      defaultValue={currentOption || "default"}
      onChange={handleChange}
      disableClearable
      autoHighlight
      autoSelect
    />
  );
}