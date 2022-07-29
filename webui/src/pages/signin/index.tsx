import { Button, createStyles, FormControl, Grid, IconButton, Input, InputAdornment, InputLabel, makeStyles, TextField, Theme, Typography } from "@material-ui/core";
import { Visibility, VisibilityOff } from "@material-ui/icons";
import { useSnackbar } from "notistack";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { selectLoggedIn, signInAsync, useReduxDispatch } from './signin.slice';
import clsx from 'clsx';
import { useSelector } from "react-redux";

export default function CoreComponent() {
  const loggedIn = useSelector(selectLoggedIn);
  // return !loggedIn ? <SignIn /> : <Redirect exact to="/" />;
  if (!loggedIn) {
    return <SignIn />;
  } else {
    return <Navigate to="/" replace />;
  }
}

export function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const dispatch = useReduxDispatch();
  const { enqueueSnackbar } = useSnackbar();
  const navigate = useNavigate();

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    dispatch(signInAsync(username, password, ['auth', 'user', 'workflow_controller']))
      .then(
        (success: boolean) => {
          enqueueSnackbar(
            success ? 'Signin successful!' : 'Error Signing in!',
            {
              variant: success ? 'success' : 'error',
              autoHideDuration: 3000,
            }
          );
          if (success) {
            setTimeout(() => {
              // forward to default page on success
              navigate('/');
            }, 1000);
          }
        },
        () => {
          enqueueSnackbar(
            'Error Signing in!',
            {
              variant: 'error',
              autoHideDuration: 3000,
            }
          );
        }
      );
  };

  const handleUsernameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(event.target.value);
  };

  const handlePasswordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const useStyles = makeStyles((theme: Theme) =>
    createStyles({
      root: {
        display: 'flex',
        flexWrap: 'wrap',
      },
      margin: {
        margin: theme.spacing(1),
      },
      withoutLabel: {
        marginTop: theme.spacing(3),
      },
      textField: {
        width: '25ch',
      },
      center: {
        left: 'auto',
        right: 'auto'
      }
    }),
  );

  const classes = useStyles();

  return (<Grid container direction="row" justify="center">
    <Grid container direction="column" className={classes.root} style={{ minHeight: '50vh' }} justifyContent="center" alignItems="center">
      <form className={classes.center} onSubmit={e => onSubmit(e)}>
        <Grid container direction="column">
          <Typography variant="h6" component="h1">
            Sign In to ChainFactory
          </Typography>
          <TextField
            aria-label="Login Username"
            label="username"
            variant="filled"
            value={username}
            onChange={handleUsernameChange}
          />
          <FormControl className={clsx(classes.margin, classes.textField)}>
            <InputLabel htmlFor="standard-adornment-password">Password</InputLabel>
            <Input
              id="standard-adornment-password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={handlePasswordChange}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    onMouseDown={handleMouseDownPassword}
                  >
                    {showPassword ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </InputAdornment>
              }
            />
          </FormControl>
          <Button type="submit" variant="contained" color="primary">SignIn</Button>
        </Grid>
      </form>
    </Grid>
  </Grid>);
}
