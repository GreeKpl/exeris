import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";


const mainReducer = combineReducers({
  player: playerReducer,
});

export default mainReducer;
