import { Button, Grid, Hidden, TextField } from '@material-ui/core';
import React, { useState } from 'react';
import Combobox from '../../../components/Combobox';

const FormComponent = ({children}) => <form noValidate autoComplete="off">{children}</form>;
const TextFieldComponent = ({label, value, onChange}) => <><TextField label={label} value={value} onChange={onChange}/><br/></>;

export interface ITaskSubTableProps {
  arguments: any;
  nodeNames: string[];
  handleStart?: {
    (
      task: string,
      selectedArguments: Map<string, string>,
      nodeSelection: string,
      tags: string[],
      namespace: string
    ): void;
  };
  task: string;
  namespace: string;
}

export function TaskSubTable(props: ITaskSubTableProps) {

  const [selectedArguments, setSelectedArguments] = useState<any>(props.arguments);
  const [selectedNode, setSelectedNode] = useState<string>("default");
  const [tags, setTags] = useState<string[]>([]);

  const gridStyle = {
    marginTop: 20,
    marginBottom: 20
  };

  const handleChange = (newValue: string, key: string) => {
    const tempArguments = JSON.parse(JSON.stringify(selectedArguments));
    tempArguments[key] = newValue;
    setSelectedArguments(tempArguments);
  };

  const handleTagsChange = (newValue: string) => {
    setTags(newValue.split(',').map((value) => value.trim()));
  };

  const formElements = Object.keys(selectedArguments).map((key) => {
    return <TextFieldComponent key={key + "123"} label={key} value={selectedArguments[key]} onChange={(event) => {handleChange(event.target.value, key);}}/>;
  });

  const handleStart = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
    event.stopPropagation();
    props.handleStart?.(props.task, selectedArguments, selectedNode, tags ? tags : [], props.namespace);
  };

  const handleNodeChange = (event: any, newValue: string | null) => {
    event.stopPropagation();
    setSelectedNode(newValue ? newValue : "");
  };
  
  return (
    <div>
      <Grid container spacing={0} justifyContent="center" alignItems="flex-start" wrap="nowrap" style={gridStyle}>
        <Hidden xsDown>
          <Grid item md={3} xs={false}>
            <h2>Input Parameter:</h2>
            <p>1. Please fill out the input parameters.</p>
            <p>2. (optional) select node to run on.</p>
            <p>3. (optional) specify tags to use for the task run.</p>
            <p>4. Press on Start to start the task.</p>
          </Grid>
        </Hidden>
        <Grid item md={3}>
          <Hidden smUp><h2>Input Parameter:</h2></Hidden>
          <FormComponent>
            {formElements}
            <br/>
            <Hidden smUp><h2>(Optional) Node Selection:</h2></Hidden>
            <Combobox label="Run on specific node" key="node_selection" options={props.nodeNames} handleChange={handleNodeChange}/>
            <Hidden smUp><h2>(Optional) Tags:</h2></Hidden>
            <TextFieldComponent key="tags" label="Tags" value={tags} onChange={(event) => {handleTagsChange(event.target.value);}}/>
            <br/><Button variant="contained" color="primary" onClick={handleStart}>Start</Button>
          </FormComponent>
        </Grid>
        <Grid item md={3}></Grid>
      </Grid>
    </div>
  );
}

export default TaskSubTable;
