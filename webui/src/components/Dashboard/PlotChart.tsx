import { Paper } from "@material-ui/core";
import React from "react";
import { Line } from 'react-chartjs-2';

export interface PlotChartProps {
  data: any;
  label: string;
};

const options = {
  scales: {
    y: {
      beginAtZero: true
    }
  },
};

export default function PlotChart(props: PlotChartProps) {
  const { data, label } = props;
  return (
    <div>
      <p>{label}</p>
      <Paper>
        <Line data={data} options={options} />
      </Paper>
    </div>
  );
};