import React from 'react';
import { RadioGroup, FormControlLabel, Radio, Typography } from '@mui/material';
import { themes } from '../../themes/themeList';
import { useAppContext } from '../../AppProvider';

const StyleOptions: React.FC = () => {
  const appContext = useAppContext();

  const handleThemeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (appContext) {
      appContext.setTheme(event.target.value);
    }
  };

  return (
    <div>
      <Typography variant="body2" color="textSecondary">
        Select a style option
      </Typography>
      <RadioGroup aria-label="style-options" name="style-options" onChange={handleThemeChange}>
        {Object.keys(themes).map((themeKey) => (
          <FormControlLabel key={themeKey} value={themeKey} control={<Radio />} label={themeKey} />
        ))}
      </RadioGroup>
    </div>
  );
};

export default StyleOptions;