import React from 'react';
import { Grid, Typography, RadioGroup, FormControlLabel, Radio, Box, Divider } from '@mui/material';
import StyleOptions from './StyleOptions';

interface SelectOptionsProps {
  selectedOption: string;
  handleOptionChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const SelectOptions: React.FC<SelectOptionsProps> = ({ selectedOption, handleOptionChange }) => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={5}>
        <Typography variant="body2" color="textSecondary">
          Select the part of the frontend you want to modify
        </Typography>
        <RadioGroup aria-label="select-options" name="select-options" value={selectedOption} onChange={handleOptionChange}>
          <FormControlLabel value="Page" control={<Radio />} label="Page" />
          <FormControlLabel value="Section" control={<Radio />} label="Section" />
          <FormControlLabel value="Component" control={<Radio />} label="Component" />
          <FormControlLabel value="Header" control={<Radio />} label="Header" />
          <FormControlLabel value="Style" control={<Radio />} label="Style" />
        </RadioGroup>
      </Grid>
      <Grid item xs={1}>
        <Divider orientation="vertical" />
      </Grid>
      <Grid item xs={6}>
        <Box>
          {selectedOption === 'Page' && <Typography>Page content goes here.</Typography>}
          {selectedOption === 'Section' && <Typography>Section content goes here.</Typography>}
          {selectedOption === 'Component' && <Typography>Component content goes here.</Typography>}
          {selectedOption === 'Header' && <Typography>Header content goes here.</Typography>}
          {selectedOption === 'Style' && <StyleOptions />}
        </Box>
      </Grid>
    </Grid>
  );
};

export default SelectOptions;