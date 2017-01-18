import socket from "../util/server";

export const REQUEST_OWN_CHARACTERS_LIST = "REQUEST_OWN_CHARACTERS_LIST";
export const UPDATE_OWN_CHARACTERS_LIST = "UPDATE_OWN_CHARACTERS_LIST";
export const UPDATE_ACHIEVEMENTS_LIST = "UPDATE_ACHIEVEMENTS_LIST";

export const requestOwnCharactersList = () => {
  return dispatch => {
    dispatch({
      type: REQUEST_OWN_CHARACTERS_LIST,
    });

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
