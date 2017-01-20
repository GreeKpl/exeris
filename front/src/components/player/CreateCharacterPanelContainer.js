import {connect} from "react-redux";
import CreateCharacterPanel from "./CreateCharacterPanel";
import {createNewCharacter} from "../../modules/player";

const mapStateToProps = (state) => {
  return {};
};

const mapDispatchToProps = (dispatch) => {
  return {
    onCreateCharacterClick: characterName => dispatch(createNewCharacter(characterName)),
  }
};

const CreateCharacterPanelContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CreateCharacterPanel);

export default CreateCharacterPanelContainer;
