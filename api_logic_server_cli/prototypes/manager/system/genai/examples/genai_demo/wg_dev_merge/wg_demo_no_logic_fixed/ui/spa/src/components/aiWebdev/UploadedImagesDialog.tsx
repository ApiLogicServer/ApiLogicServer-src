import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Button, List, ListItem } from '@mui/material';
import PaperComponent from './PaperComponent';

const UploadedImagesDialog = ({ isImageDialogOpen, toggleImageDialog, imageNames }) => {
  return (
    <Dialog
      open={isImageDialogOpen}
      onClose={toggleImageDialog}
      PaperComponent={PaperComponent}
      aria-labelledby="uploaded-images-dialog-title"
      maxWidth="md"
      fullWidth
    >
      <DialogTitle style={{ cursor: 'move' }} id="uploaded-images-dialog-title">
        Uploaded Images
      </DialogTitle>
      <DialogContent className="custom-scrollbar" sx={{ height: '350px', overflowY: 'auto' }}>
        <List>
          {imageNames.map((name, index) => (
            <ListItem key={index}>{name}</ListItem>
          ))}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={toggleImageDialog} color="secondary" variant="outlined" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UploadedImagesDialog;