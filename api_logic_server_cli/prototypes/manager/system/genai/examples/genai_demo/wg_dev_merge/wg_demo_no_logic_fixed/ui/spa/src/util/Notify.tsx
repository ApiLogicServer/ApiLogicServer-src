import React, { useState } from 'react';
import Snackbar from '@mui/material/Snackbar';
import SnackbarContent from '@mui/material/SnackbarContent';
import { makeStyles, useTheme } from '@mui/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { green } from '@mui/material/colors';

const useStyles = makeStyles((theme) => ({
    success: {
        backgroundColor:"white",
    },
    icon: {
        fontSize: 35,
    },
    root: {
        width: '100%',
        maxWidth: 345,
        backgroundColor: theme.palette?.background.paper,
    },
    closeButton: {
        position: 'absolute',
        right: 8,
        top: 8,
        color: theme.palette?.grey[500],
    },
}));

const Notify = ({open, message, timeout}:{open:boolean, message: string, timeout?: number}) => {
    const theme = useTheme();
    const classes = useStyles({ theme });
    const [isOpen, setIsOpen] = useState(open);

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setIsOpen(false);
    };

    const handleClick = () => {
        setIsOpen(true);
    };

    return (
        <div>
            
            <Snackbar
                open={isOpen}
                autoHideDuration={timeout || 3000}
                onClose={handleClose}
                message={message}
                action={
                    <div>
                        <span style={{ color: 'inherit', paddingRight:'1em' }} onClick={() => handleClose(null, 'clickaway')}>x</span>
                    </div>
                }
                className={classes.success}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            />
        </div>
    );
};

export default Notify;