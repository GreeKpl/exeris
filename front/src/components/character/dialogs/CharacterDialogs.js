import React from "react";
import {ReadableEntityModalContainer} from "./ReadableEntityModalContainer";
import {DIALOG_READABLE} from "../../../modules/details";

export const CharacterDialogs = ({dialogType, targetId, characterId}) => {
  switch (dialogType) {
    case DIALOG_READABLE:
      return <ReadableEntityModalContainer characterId={characterId} entityId={targetId}/>;
    default:
      return null;
  }
};
