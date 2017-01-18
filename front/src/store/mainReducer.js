import playerReducer from "../player/reducers";
import {combineReducers} from "redux-immutable";
import {ownCharactersListReducer} from "../app/reducers";


const mainReducer = combineReducers({
  player: playerReducer,
  ownCharactersList: ownCharactersListReducer,
});

export default mainReducer;
