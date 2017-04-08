import {connect} from "react-redux";
import Equipment from "./Equipment";
import * as Immutable from "immutable";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";

const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    equipment: myCharacterInfo.get("equipment", Immutable.Map()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const EquipmentContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Equipment);

export default EquipmentContainer;
