import { AutocompleteChangeDetails, AutocompleteChangeReason } from "@material-ui/lab";
import React from "react";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import Combobox from "../../../../components/Combobox";
import { selectNamespace, selectNamespaces, selectNamespacesError, selectNamespacesFetching, setNamespace } from "./NamespaceSelector.reducer";
import { fetchNamespaces } from "./NamespaceSelector.service";

export default function NamespaceSelector() {
  const dispatch = useDispatch();
  const namespaces = useSelector(selectNamespaces);
  const namespacesFetching = useSelector(selectNamespacesFetching);
  const namespacesError = useSelector(selectNamespacesError);
  const namespace = useSelector(selectNamespace);

  useEffect(() => {
    if (namespacesFetching) {
      return;
    }
    if (namespacesError) {
      return;
    }
    dispatch(fetchNamespaces());
  }, [namespacesFetching, namespacesError, dispatch]);

  if (namespaces) {
    const handleChange = (event: React.ChangeEvent<{}>, value: any, reason: AutocompleteChangeReason, details?: AutocompleteChangeDetails<any> | undefined) => {
      dispatch(setNamespace(value));
    };

    return <Combobox options={namespaces} currentOption={namespace} label="Select Namespace" handleChange={handleChange}/>
  }
  return <></>;
}