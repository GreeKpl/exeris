import * as Immutable from "immutable";
import socket from "../util/server";

export const UPDATE_OWN_CHARACTERS_LIST = "exeris-front/player/UPDATE_OWN_CHARACTERS_LIST";
export const UPDATE_ACHIEVEMENTS_LIST = "exeris-front/player/UPDATE_ACHIEVEMENTS_LIST";

export const requestOwnCharactersList = () => {
  return dispatch => {
    socket.request("player.get_characters_list", characterslist => {
      dispatch(updateOwnCharactersList(characterslist));
    });
  }
};

export const updateOwnCharactersList = (charactersList) => {
  return {
    type: UPDATE_OWN_CHARACTERS_LIST,
    charactersList: charactersList,
  };
};

export const createNewCharacter = (characterName) => {
  return dispatch => {
    socket.request("player.create_new_character", characterName, () => {
      dispatch(requestOwnCharactersList());
    });
  }
};

export const requestAchievementsList = () => {
  return dispatch => {
    socket.request("player.get_achievements_list", achievementsList => {
      dispatch(updateAchievementsList(achievementsList));
    });
  }
};

export const updateAchievementsList = (achievementsList) => {
  return {
    type: UPDATE_ACHIEVEMENTS_LIST,
    achievementsList,
  };
};


export const playerReducer = (state = Immutable.fromJS({achievements: [], ownCharacters: []}), action) => {
  switch (action.type) {
    case UPDATE_ACHIEVEMENTS_LIST:
      return state.set("achievements", Immutable.fromJS(action.achievementsList));
    case UPDATE_OWN_CHARACTERS_LIST:
      return state.set("ownCharacters", Immutable.fromJS(action.charactersList));
    default:
      return state;
  }
};

export const getOwnCharactersList = state => state.get("ownCharacters");

export const getAchievementsList = state => state.get("achievements");

export const fromPlayerState = state => state.get("player");
