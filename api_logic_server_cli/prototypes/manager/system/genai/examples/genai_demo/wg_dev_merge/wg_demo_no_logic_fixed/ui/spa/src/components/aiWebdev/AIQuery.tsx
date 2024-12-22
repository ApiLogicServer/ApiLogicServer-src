import React, { useState } from 'react';
import { IconButton } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import Draggable from 'react-draggable';
import { useDataProvider } from 'react-admin';
import MainDialog from './MainDialog.tsx';
import SaveDialog from './SaveDialog';
import UploadedImagesDialog from './UploadedImagesDialog';
import handleAIQuery from '../sections/AIQueryHandler.tsx';
import { getAppId } from '../../util/util.tsx';
//import './style/AIQuery.css';

const AIQuery = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [aiPromptValue, setAiPromptValue] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');
  const [selectedTab, setSelectedTab] = useState(0);
  const [imageNames, setImageNames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState('Component');
  const [isImageDialogOpen, setIsImageDialogOpen] = useState(false);
  const [isSaveDialogOpen, setIsSaveDialogOpen] = useState(false);
  const [saveName, setSaveName] = useState('');
  const dataProvider = useDataProvider();
  const [refreshVersion, setRefreshVersion] = useState(0);

  const toggleDialog = () => {
    setIsDialogOpen(!isDialogOpen);
  };

  const toggleImageDialog = () => {
    setIsImageDialogOpen(!isImageDialogOpen);
  };

  const toggleSaveDialog = () => {
    setIsSaveDialogOpen(!isSaveDialogOpen);
  };

  const handleChange = (event: { target: { value: React.SetStateAction<string>; }; }) => {
    setAiPromptValue(event.target.value);
  };

  const handleImagePromptChange = (event: { target: { value: React.SetStateAction<string>; }; }) => {
    setImagePrompt(event.target.value);
  };

  const handleSaveNameChange = (event: { target: { value: React.SetStateAction<string>; }; }) => {
    setSaveName(event.target.value);
  };

  const handleSubmit = async () => {
    if (!aiPromptValue) {
      console.log("Submit without prompt");
      return;
    }
    setLoading(true);
    await handleAIQuery(dataProvider, `${aiPromptValue}`);
    setLoading(false);
  };

  const handleSave = async () => {
    setLoading(true);
    await dataProvider.create('SPAComponent', {
      data: {
        Type: "save",
        name: saveName,
        project_id: getAppId(),
      }
    });
    setLoading(false);
    toggleSaveDialog();
    setRefreshVersion(refreshVersion + 1);
  };

  const handleTabChange = (_event: any, newValue: React.SetStateAction<number>) => {
    setSelectedTab(newValue);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files[0]) {
      const file = files[0];
      setImageNames([...imageNames, file.name]);
      alert(`Uploaded Image: ${file.name}`);
    }
  };

  const handleOptionChange = (event: { target: { value: React.SetStateAction<string>; }; }) => {
    setSelectedOption(event.target.value);
  };

  return (
    <div>
      <Draggable>
        <div
          style={{
            display: 'inline-block',
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            zIndex: 9999,
            background: 'transparent',
          }}
        >
          <IconButton
            onClick={toggleDialog}
            color="primary"
            style={{
              width: '70px',
              height: '70px',
              backgroundColor: 'transparent',
              borderRadius: '50%',
              padding: 0,
              border: '2px solid white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              '&:focus, &:active': {
                borderColor: 'white',
                outline: 'none',
              },
            }}
          >
            <ChatIcon style={{ fontSize: '36px' }} />
          </IconButton>
        </div>
      </Draggable>

      <MainDialog
        isDialogOpen={isDialogOpen}
        toggleDialog={toggleDialog}
        selectedTab={selectedTab}
        handleTabChange={handleTabChange}
        aiPromptValue={aiPromptValue}
        handleChange={handleChange}
        handleSubmit={handleSubmit}
        loading={loading}
        selectedOption={selectedOption}
        handleOptionChange={handleOptionChange}
        imagePrompt={imagePrompt}
        handleImagePromptChange={handleImagePromptChange}
        handleImageUpload={handleImageUpload}
        imageNames={imageNames}
        toggleImageDialog={toggleImageDialog}
        refreshVersion={refreshVersion}
        toggleSaveDialog={toggleSaveDialog}
      />

      <SaveDialog
        isSaveDialogOpen={isSaveDialogOpen}
        toggleSaveDialog={toggleSaveDialog}
        saveName={saveName}
        handleSaveNameChange={handleSaveNameChange}
        handleSave={handleSave}
        loading={loading}
      />

      <UploadedImagesDialog
        isImageDialogOpen={isImageDialogOpen}
        toggleImageDialog={toggleImageDialog}
        imageNames={imageNames}
      />
    </div>
  );
};

export default AIQuery;