import React from 'react';
import { Box, TextField, Backdrop, CircularProgress, Typography, RadioGroup, FormControlLabel, Radio, Button } from '@mui/material';

const AIPromptTab = ({ aiPromptValue, handleChange, handleSubmit, loading, handleOptionChange }) => {
    const [selectedOption, setSelectedOption] = React.useState('generate');
  return (
    <Box position="relative">
      <TextField
        value={aiPromptValue}
        onChange={handleChange}
        label="Prompt"
        multiline
        rows={5}
        variant="outlined"
        fullWidth
        InputProps={{ style: { minHeight: '100px' } }}
      />
      {loading && (
        <Backdrop sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: (theme) => theme.zIndex.drawer + 1, color: '#fff' }} open={loading}>
          <CircularProgress color="inherit" />
        </Backdrop>
      )}
      <Typography variant="body2" color="textSecondary" style={{ marginTop: '8px' }}>
        {selectedOption === 'generate' ? 'Specify how you want to modify the page' : 'Ask information about this page design and backend resources'}
      </Typography>
      <RadioGroup aria-label="options" name="options" value={selectedOption} onChange={handleOptionChange} row sx={{ marginTop: '8px' }}>
        <FormControlLabel value="generate" control={<Radio />} label="Generate" />
        <FormControlLabel value="question" control={<Radio />} label="Question" />
      </RadioGroup>
      <Button onClick={handleSubmit} color="primary" variant="outlined" disabled={loading || !aiPromptValue} sx={{ '&:focus, &:active': { borderColor: 'white', outline: 'none' } }}>
        Submit
      </Button>
    </Box>
  );
};

export default AIPromptTab;