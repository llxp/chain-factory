import React from "react";
import Autocomplete, { AutocompleteChangeDetails, AutocompleteChangeReason } from '@material-ui/lab/Autocomplete';
import TextField from "@material-ui/core/TextField";

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
  const defaultOptions: IComboboxItem[] = [defaultOption, ...options];
  return (
    <Autocomplete
      options={defaultOptions}
      getOptionLabel={(option) => option.display || 'default'}
      style={{ width: 300 }}
      renderInput={(params) => <TextField {...params} label={label} variant="outlined" size="small"/>}
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