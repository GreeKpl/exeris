import {browserHistory} from 'react-router';

export const routerLink = event => {
  event.preventDefault();
  browserHistory.push(event.target.href);
};
