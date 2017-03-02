import React from "react";
import {
  DETAILS_CHARACTER,
  DETAILS_COMBAT,
} from "../../../modules/topPanel";
import CombatTopPanelContainer from "./CombatTopPanelContainer";
import CharacterPanelContainer from "./CharacterPanelContainer";

/**
 * @return {XML|null}
 */
const TopPanel = ({characterId, detailsType}) => {
  switch (detailsType) {
    case DETAILS_COMBAT:
      return <CombatTopPanelContainer characterId={characterId}/>;
      break;
    case DETAILS_CHARACTER:
      return <CharacterPanelContainer characterId={characterId}/>;
      break;
    default:
      return null;
  }
};


export default TopPanel;
