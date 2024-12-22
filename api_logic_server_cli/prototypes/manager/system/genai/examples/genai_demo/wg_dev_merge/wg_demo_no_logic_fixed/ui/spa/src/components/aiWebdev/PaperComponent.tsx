import React from 'react';
import { Paper } from '@mui/material';
import Draggable from 'react-draggable';

const PaperComponent = (props) => {
  return (
    <Draggable handle="#draggable-dialog-title" cancel={'[class*="MuiDialogContent-root"]'}>
      <Paper {...props} />
    </Draggable>
  );
};

export default PaperComponent;