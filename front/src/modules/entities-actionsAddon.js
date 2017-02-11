import socket from "../util/server";
import {
  requestRefreshEntity,
  deselectEntity,
  selectEntityAction,
  clearSelectedEntityAction,
  requestRootEntities
} from "./entities";

export const ENTITY_ACTION_TAKE = "ENTITY_ACTION_TAKE";
export const ENTITY_ACTION_DROP = "ENTITY_ACTION_DROP";
export const ENTITY_ACTION_GIVE = "ENTITY_ACTION_GIVE";
export const ENTITY_ACTION_EAT = "ENTITY_ACTION_EAT";
export const ENTITY_ACTION_PUT_INTO_STORAGE = "ENTITY_ACTION_PUT_INTO_STORAGE";
export const ENTITY_ACTION_BIND_TO_VEHICLE = "ENTITY_ACTION_BIND_TO_VEHICLE";


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

  socket.on("character.put_into_storage_setup", (characterId, maxAmount, storages) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_PUT_INTO_STORAGE, {
      maxAmount: maxAmount,
      storages: storages,
    }));
  });

  socket.on("character.put_into_storage_after", (characterId, itemIds, storageId) => {
    for (let itemId of itemIds) {
      dispatch(standardAfterEntityAction(characterId, itemId));
    }
    dispatch(requestRefreshEntity(characterId, storageId));
  });

  socket.on("character.attack_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.unbind_from_vehicle_after", (characterId, entityIds) => {
    for (let entityId of entityIds) {
      dispatch(standardAfterEntityAction(characterId, entityId));
    }
  });

  socket.on("character.bind_to_vehicle_setup", (characterId, entities) => {
    dispatch(selectEntityAction(characterId, ENTITY_ACTION_BIND_TO_VEHICLE, entities));
  });

  socket.on("character.bind_to_vehicle_after", (characterId, entityIds) => {
    for (let entityId of entityIds) {
      dispatch(standardAfterEntityAction(characterId, entityId));
    }
  });

  socket.on("character.start_boarding_ship_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.start_unboarding_from_ship_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.start_burying_entity_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.start_taming_animal_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.toggle_closeable_after", (characterId, entityId) => {
    dispatch(standardAfterEntityAction(characterId, entityId));
  });

  socket.on("character.move_to_location_after", (characterId) => { // enter
    dispatch(requestRootEntities(characterId));
  });

  socket.on("character.go_to_location_after", (characterId) => { // travel to
    console.log("TODO GO TO LOCATION");
  });

  socket.on("character.show_readable_contents_after", (characterId, readableEntity) => {
    console.log("TODO READABLE ENTITY");
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
