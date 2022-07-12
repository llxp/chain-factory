import { red } from '@material-ui/core/colors';
import { unstable_createMuiStrictModeTheme as createTheme } from '@material-ui/core/styles';
// A custom theme for this app
const theme = createTheme({
  palette: {
    type: 'light',
    primary: {
      main: '#e91e63',  // e91e63
      light: '#61dafb',  // 61dafb
      dark: '#e91e63',  // e91e63
      contrastText: '#ffffffff',  // 383838
    },
    secondary: {
      main: '#303030',  // 303030
      light: '#fff',  // 61dafb
      dark: '#383838',  // 303030
    },
    error: {
      main: red.A400,
    },
    background: {
      default: '#ffffffff',  // 303030, 383838
      paper: '#d0d0d0'
    },
  },
  overrides: {
    MuiPaper: {
      root: {
        //padding: '20px 10px',
        //margin: '10px',
        //backgroundColor: '#fff', // 5d737e
      },
    },
    MuiButton: {
      root: {
        //margin: '5px',
      },
    },
    MuiCheckbox: {
      colorSecondary: {
        color: '#000000',
        '&$checked': {
          color: '#000000',
        },
      },
    }
  },
});
export default theme;