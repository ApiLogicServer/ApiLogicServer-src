import React from 'react';
import { Dialog, DialogActions, DialogContent, DialogTitle, Typography, IconButton, Tabs, Tab, Box, TextField, Button, Backdrop, CircularProgress, RadioGroup, FormControlLabel, Radio, Grid, Link, List, ListItem } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import PaperComponent from './PaperComponent';
import TabPanel from './TabPanel';
import ComponentList from './ComponentList';
import AIPromptTab from './AIPromptTab';
import { getAppId } from '../../util/util';
import SelectOptions from './SelectOptions';
  

interface MainDialogProps {
  isDialogOpen: boolean;
  toggleDialog: () => void;
  selectedTab: number;
  handleTabChange: (event: React.SyntheticEvent, newValue: number) => void;
  aiPromptValue: string;
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: () => void;
  loading: boolean;
  selectedOption: string;
  handleOptionChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  imagePrompt: string;
  handleImagePromptChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleImageUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  imageNames: string[];
  toggleImageDialog: () => void;
  refreshVersion: number;
  toggleSaveDialog: () => void;
}

const MainDialog: React.FC<MainDialogProps> = ({ isDialogOpen, toggleDialog, selectedTab, handleTabChange, aiPromptValue, handleChange, handleSubmit, loading, selectedOption, handleOptionChange, imagePrompt, handleImagePromptChange, handleImageUpload, imageNames, toggleImageDialog, refreshVersion, toggleSaveDialog }) => {

  const appName = sessionStorage.getItem('appName') || getAppId();
  const appId = (
    <Typography variant='caption' sx={{ color: "#ccc", verticalAlign: "left", width: "90%" }}>
      <IconButton onClick={() => {
        localStorage.removeItem('appId');
        document.location.reload();
      }} sx={{ color: "#ccc", padding: 0, marginRight: '8px' }}>
        <SettingsIcon />
      </IconButton>
    </Typography>
  );

  return (
    <Dialog
      open={isDialogOpen}
      onClose={toggleDialog}
      PaperComponent={PaperComponent}
      aria-labelledby="draggable-dialog-title"
      maxWidth="md"
      fullWidth
    >
      <DialogTitle style={{ cursor: 'move', display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }} id="draggable-dialog-title">
        <span style={{ flexGrow: 1, textAlign: 'left' }}>AI WebDev <span style={{color:"#ccc", fontStyle:"italic"}} > &nbsp;
            {selectedOption}</span></span>
        <Link href={document.location.href.split('#')[0]} sx={{ color: "#ccc", textDecoration: 'none', fontSize: '0.6em' }}>
          {appName || appId}
        </Link>
      </DialogTitle>
      <DialogContent className="custom-scrollbar" sx={{ height: '380px', overflowY: 'auto' }}>
        <Tabs value={selectedTab} onChange={handleTabChange} aria-label="basic tabs example">
          <Tab label="Select" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }} />
          <Tab label="AI Prompt" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }} />
          <Tab label="Images" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }} />
          <Tab label="Prompts" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }} />
          <Tab label="Templates" sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }} />
        </Tabs>
        <TabPanel value={selectedTab} index={0}>
            <SelectOptions selectedOption={selectedOption} handleOptionChange={handleOptionChange} />
        </TabPanel>
        <TabPanel value={selectedTab} index={1}>
          <AIPromptTab
            aiPromptValue={aiPromptValue}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
            loading={loading}
            handleOptionChange={handleOptionChange}
          />
        </TabPanel>
        <TabPanel value={selectedTab} index={2}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                value={imagePrompt}
                onChange={handleImagePromptChange}
                label="Image Prompt"
                multiline
                rows={2}
                variant="outlined"
                fullWidth
                InputProps={{ style: { minHeight: '50px' } }}
              />
            </Grid>
            <Grid item xs={12}>
              <Button variant="outlined" color="primary" sx={{ width: '12em', '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
                Generate Image
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Button variant="outlined" component="label" sx={{ width: '12em', '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
                Upload File
                <input type="file" hidden onChange={handleImageUpload} />
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Link component="button" color="textSecondary" onClick={toggleImageDialog} style={{ marginBottom: '8px', textDecoration: 'none' }} sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
                Uploaded Images
              </Link>
              <List>
                {imageNames.map((name, index) => (
                  <ListItem key={index}>{name}</ListItem>
                ))}
              </List>
            </Grid>
          </Grid>
        </TabPanel>
        <TabPanel value={selectedTab} index={3}>
          <ComponentList type={"prompt"} key={refreshVersion} />
        </TabPanel>
        <TabPanel value={selectedTab} index={4}>
          <ComponentList type={"template"} key={refreshVersion} />
        </TabPanel>
      </DialogContent>
      <DialogActions>
        {appId}
        <Button onClick={toggleSaveDialog} variant="outlined" disabled={loading } >
          Save
        </Button>
        <Button onClick={toggleDialog} variant="outlined" >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default MainDialog;