export function isXsScreen() {
  //console.log(window.innerWidth);
  return window.innerWidth < 576;
}

export function isSmScreen() {
  //console.log(window.innerWidth);
  return window.innerWidth >= 576 && !isLgScreen();
}

export function isMdScreen() {
  //console.log(window.innerWidth);
  return window.innerWidth >= 768 && !isLgScreen();
}

export function isLgScreen() {
  //console.log(window.innerWidth);
  return window.innerWidth >= 992 && !isXlScreen();
}

export function isXlScreen() {
  //console.log(window.innerWidth);
  return window.innerWidth >= 1200;
}

export function isXLhScreen() {
  return window.innerHeight >= 1000;
}

export function isLGhScreen() {
  return window.innerHeight >= 700;
}

export function isMdhScreen() {
  return window.innerHeight >= 1000;
}

export function getWindowDimensions() {
  const { innerWidth: width, innerHeight: height } = window;
  return {
    width,
    height
  };
}