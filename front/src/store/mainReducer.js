import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";
import {decoratedEventsReducer} from "../modules/events";
import {decoratedCharactersAroundReducer} from "../modules/charactersAround";
import {decoratedSpeechReducer} from "../modules/speech";
import {decoratedDetailsReducer} from "../modules/details";
import {decoratedEntitiesReducer} from "../modules/entities";
import {notificationsReducer} from "../modules/notifications";
import {decoratedRecipesReducer} from "../modules/recipes";
import {reducer as formReducer} from "redux-form/immutable";
import {decoratedDynamicNamesReducer} from "../modules/dynamicNames";
import {decoratedTravelReducer} from "../modules/travel";
import {decoratedMyCharacterReducer} from "../modules/myCharacter";
import {createResponsiveStateReducer} from "redux-responsive";
import {transform} from 'lodash';

const mainReducer = combineReducers({
  player: playerReducer,
  events: decoratedEventsReducer,
  charactersAround: decoratedCharactersAroundReducer,
  speech: decoratedSpeechReducer,
  details: decoratedDetailsReducer,
  entities: decoratedEntitiesReducer,
  myCharacter: decoratedMyCharacterReducer,
  notifications: notificationsReducer,
  recipes: decoratedRecipesReducer,
  travel: decoratedTravelReducer,
  dynamicNames: decoratedDynamicNamesReducer,
  form: formReducer,
  browser: createResponsiveStateReducer(null, {
    extraFields: ({greaterThan, lessThan, is}) => ({
      atLeast: transform(greaterThan, (result, value, mediaType) => {
        result[mediaType] = value || is[mediaType]
      }, {}),
      atMost: transform(lessThan, (result, value, mediaType) => {
        result[mediaType] = value || is[mediaType]
      }, {}),
    }),
  }),
});

export default mainReducer;
