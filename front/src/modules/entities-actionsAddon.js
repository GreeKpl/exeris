import socket from "../util/server";
import {requestRefreshEntity, deselectEntity, selectEntityAction, clearSelectedEntityAction} from "./entities";

export const ENTITY_ACTION_TAKE = "ENTITY_ACTION_TAKE";
export const ENTITY_ACTION_DROP = "ENTITY_ACTION_DROP";
export const ENTITY_ACTION_GIVE = "ENTITY_ACTION_GIVE";
export const ENTITY_ACTION_EAT = "ENTITY_ACTION_EAT";

export const setUpSocketioListeners = dispatch => {

  socket.on("character.take_item_setup", (characterId, maxAmount) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_TAKE, {maxAmount: maxAmount}));
  });

  socket.on("character.take_item_after", (characterId, itemIds) => {
    for (let itemId of itemIds) {
      dispatch(standardAfterEntityAction(characterId, itemId));
    }
  });

  socket.on("character.drop_item_setup", (characterId, maxAmount) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_DROP, {maxAmount: maxAmount}));
  });

  socket.on("character.drop_item_after", (characterId, itemIds) => {
    for (let itemId of itemIds) {
      dispatch(standardAfterEntityAction(characterId, itemId));
    }
  });

  socket.on("character.give_item_setup", (characterId, maxAmount, receivers) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_GIVE, {receivers: receivers, maxAmount: maxAmount}));
  });

  socket.on("character.give_item_after", (characterId, itemIds) => {
    for (let itemId of itemIds) {
      dispatch(standardAfterEntityAction(characterId, itemId));
    }
  });

  socket.on("character.eat_setup", (characterId, maxAmount) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_EAT, {maxAmount: maxAmount}));
  });

  socket.on("character.eat_after", (characterId, itemIds) => {
    for (let itemId of itemIds) {
      dispatch(standardAfterEntityAction(characterId, itemId));
    }
  });

  socket.on("after_unbind_from_vehicle", (entities) => {
    // for (let i = 0; i < entities.length; i++) {
    //   $.publish("entities:refresh_entity_info", entities[i]);
    // }
  });

  socket.on("after_start_boarding_ship", (entity_id) => {
    // $.publish("entities:refresh_entity_info", entity_id);
  });

  socket.on("after_start_unboarding_from_ship", (entity_id) => {
    // $.publish("entities:refresh_entity_info", entity_id);
  });
};


export const performEntityAction = (characterId, endpoint, entityIds, ...params) => {
  return dispatch => {
    socket.request(endpoint, characterId, entityIds, ...params);
  }
};


const standardAfterEntityAction = (characterId, itemId) => {
  return dispatch => {
    dispatch(requestRefreshEntity(characterId, itemId));
    dispatch(clearSelectedEntityAction(characterId));
    dispatch(deselectEntity(characterId, itemId));
  };
};

