import { Button, createStyles, FormControl, Grid, IconButton, Input, InputAdornment, InputLabel, makeStyles, TextField, Theme, Typography } from "@material-ui/core";
import { Visibility, VisibilityOff } from "@material-ui/icons";
import { useSnackbar } from "notistack";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { getUserProfileAsync, selectLoggedIn, setLoggedIn, signInAsync, useReduxDispatch } from './signin.slice';
import clsx from 'clsx';
import { useSelector } from "react-redux";
import { UserProfile } from "../../models";

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
    // first sign in using only the auth scope
    // then get the user profile to obtain all scopes the user has access to
    // then sign in again using all available scopes

    // sign in using only the auth/user scope to be able to get the user profile
    dispatch(signInAsync(username, password, ['auth', 'user']))
    .then((success: boolean) => {
      if (success) {
        // get user profile, to obtain all available scopes, the user can request
        dispatch(getUserProfileAsync()).then((user: UserProfile | null) => {
          if (user) {
            // sign in again, using all available scopes
            dispatch(signInAsync(username, password, user.scopes)).then((success: boolean) => {
              // show success message on success
              showSuccessMessage();
              if (success) {
                // set logged in state
                dispatch(setLoggedIn(true));
                // wait a second, then forward to default page
                setTimeout(() => {
                  // forward to default page on success
                  navigate('/');
                }, 1000);
              }
            }, () => {
              // show error message on failure
              showErrorMessage("Error Signing in!");
            });
          } else {
            // show error message on failure to get user profile, because user profile is null
            showErrorMessage("Error getting user profile!");
          }
        }, () => {
          // show error message on failure to get user profile
          showErrorMessage("Error getting user profile!");
        });
      } else {
        // show error message on failure to sign in using only the auth/user scope
        showErrorMessage("Error Signing in!");
      }
    }, () => {
      // show error message on failure to sign in using only the auth/user scope
      showErrorMessage("Error Signing in!");
    });
  };

  const showSuccessMessage = () => {
    enqueueSnackbar(
      'Signin successful!',
      {
        variant: 'success',
        autoHideDuration: 3000,
      }
    );
  };

  const showErrorMessage = (message: string) => {
    enqueueSnackbar(
      `${message}!`,
      {
        variant: 'error',
        autoHideDuration: 3000,
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

  return (<Grid container direction="row" justifyContent="center">
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
