import { IconButton, Tooltip } from "@material-ui/core";
import { AutocompleteChangeDetails, AutocompleteChangeReason } from "@material-ui/lab";
import React from "react";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import Combobox, { IComboboxItem } from "../../../../components/Combobox";
import NamespaceAddDialog from "./NamespaceAddDialog";
import NamespaceEditor from "./NamespaceEditor";
import { selectDisabledNamespaces, selectNamespace, selectNamespaces, selectNamespacesError, selectNamespacesFetching, setNamespace, setNamespaceAddDialogOpen, setNamespaceDisabled, setNamespaceEditorOpen } from "./NamespaceSelector.reducer";
import { fetchNamespaces } from "./NamespaceSelector.service";

export default function NamespaceSelector() {
  const dispatch = useDispatch();
  const namespaces = useSelector(selectNamespaces);
  const namespacesFetching = useSelector(selectNamespacesFetching);
  const namespacesError = useSelector(selectNamespacesError);
  const namespace = useSelector(selectNamespace);
  const disabledNamespaces = useSelector(selectDisabledNamespaces);

  useEffect(() => {
    dispatch(fetchNamespaces());
  }, [dispatch]);

  if (namespacesFetching) {
    return <div>Loading...</div>;
  }

  if (namespacesError) {
    return <Combobox options={[{
      display: "Error",
      value: "Error"
    }]} currentOption={{
      display: namespace,
      value: namespace,
    }} label="Select Namespace" handleChange={() => {}} key="cb"/>
  }

  if (!namespacesFetching && !namespacesError) {
    
    const handleChange = (event: React.ChangeEvent<{}>, value: IComboboxItem, reason: AutocompleteChangeReason, details?: AutocompleteChangeDetails<any> | undefined) => {
      if (value.group && value.group === "Disabled") {
        dispatch(setNamespaceDisabled(true));
      } else {
        dispatch(setNamespaceDisabled(false));
      }
      dispatch(setNamespace(value?.value || value.display));
    };

    const NamespaceButtons = () => {
      const defaultNamespaceSelected = namespace === "default" || namespace === "" || namespace === "all";
      const ManageNamespaceButton = () => {
        return defaultNamespaceSelected ? <IconButton color="inherit" aria-label="Manage Namespace" onClick={()=>dispatch(setNamespaceEditorOpen(true))} disabled={true}>
        <i className="material-icons">settings</i>
      </IconButton> : <Tooltip title="Manage Namespace Access" arrow key="mna">
      <IconButton color="inherit" aria-label="Manage Namespace" onClick={()=>dispatch(setNamespaceEditorOpen(true))} disabled={false}>
        <i className="material-icons">settings</i>
      </IconButton>
    </Tooltip>;
      }
      return <>
        <ManageNamespaceButton />
        <Tooltip title="Add New Namespace" arrow key="ann">
          <IconButton color="inherit" aria-label="Add Namespace" onClick={()=>dispatch(setNamespaceAddDialogOpen(true))}>
            <i className="material-icons">add</i>
          </IconButton>
        </Tooltip>
      </>;
    }

    const enabledOptions = (namespaces || []).map((option) => {
      return {
        display: option,
        value: option
      }
    });

    const disabledOptions = (disabledNamespaces || []).map((option) => {
      return {
        display: option,
        value: option,
        group: "Disabled"
      }
    });

    const options = [...enabledOptions, ...disabledOptions];

    return <>
      <Combobox options={options} currentOption={{
        display: namespace,
        value: namespace,
      }} label="Select Namespace" handleChange={handleChange} key="cb"/>
      <NamespaceButtons key="nb"/>
      <NamespaceEditor key="ne"/>
      <NamespaceAddDialog key="na"/>
    </>
  }
  return <></>;
}