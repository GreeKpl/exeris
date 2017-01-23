import React from "react";
import {
  DETAILS_CHARACTER,
  DETAILS_COMBAT,
} from "../../../modules/topPanel";
import CombatTopPanelContainer from "./CombatTopPanelContainer";
import CharacterTopPanelContainer from "./CharacterTopPanelContainer";

/**
 * @return {XML|null}
 */
const TopPanel = ({characterId, detailsType}) => {
  switch (detailsType) {
    case DETAILS_COMBAT:
      return <CombatTopPanelContainer characterId={characterId}/>;
      break;
    case DETAILS_CHARACTER:
      return <CharacterTopPanelContainer characterId={characterId}/>;
      break;
    default:
      return null;
  }
};


export default TopPanel;
