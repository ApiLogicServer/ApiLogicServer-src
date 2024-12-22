import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, TextField, Button } from '@mui/material';
import PaperComponent from './PaperComponent';

const SaveDialog = ({ isSaveDialogOpen, toggleSaveDialog, saveName, handleSaveNameChange, handleSave, loading }) => {
  return (
    <Dialog
      open={isSaveDialogOpen}
      onClose={toggleSaveDialog}
      PaperComponent={PaperComponent}
      aria-labelledby="save-dialog-title"
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle style={{ cursor: 'move' }} id="save-dialog-title">
        Save Prompt
      </DialogTitle>
      <DialogContent>
        <TextField
          value={saveName}
          onChange={handleSaveNameChange}
          label="Name"
          variant="outlined"
          fullWidth
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleSave} color="primary" variant="outlined" disabled={loading || !saveName} sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
          Save
        </Button>
        <Button onClick={toggleSaveDialog} color="secondary" variant="outlined" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SaveDialog;