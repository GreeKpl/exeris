import {connect} from "react-redux";
import {
  canBeControlled,
  fromTravelState,
  changeMovementDirection,
  stopMovement,
  getMovementAction,
  requestTravelState
} from "../../../modules/travel";
import {parseHtmlToComponents} from "../../../util/parseDynamicName";

import React from "react";
import {Panel, Form, FormGroup, FormControl, ControlLabel, Button} from "react-bootstrap";


const SetDirectionForm = ({onSubmitDirection, onSubmitStop, onChange, direction}) => {
  return <Form autoComplete="off" inline>
    <FormGroup controlId="travelDirection">
      <ControlLabel>Direction</ControlLabel>
      {' '}
      <FormControl type="number" placeholder="Set degrees..."
                   onChange={onChange} value={direction}/>
    </FormGroup>
    {' '}
    <Button type="submit" onClick={onSubmitDirection}>
      Set travel direction
    </Button>
    <Button onClick={onSubmitStop}>Stop</Button>
  </Form>;
};


/**
 * @return {string}
 */
const MovementInfo = ({movementAction}) => {
  return <p>{movementAction}</p>;
};

export class ControlMovement extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      direction: "",
    };

    this.handleSubmitDirection = this.handleSubmitDirection.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmitStop = this.handleSubmitStop.bind(this);
  }

  handleSubmitDirection(event) {
    event.preventDefault();
    this.props.onSubmitDirection(this.state.direction);
  }

  handleSubmitStop(event) {
    event.preventDefault();
    this.props.onSubmitStop();
  }

  handleChange(event) {
    const newValue = event.target.value;
    this.setState({
      direction: newValue,
    });
  }

  componentDidMount() {
    this.props.requestState();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.characterId !== this.props.characterId) {
      this.props.requestState();
    }
  }

  render() {
    return (
      this.props.canBeControlled ?
        <Panel header="Control movement">
          {this.props.movementAction && <MovementInfo
            movementAction={this.props.movementAction}/>}
          <SetDirectionForm onSubmitStop={this.handleSubmitStop}
                            onSubmitDirection={this.handleSubmitDirection}
                            onChange={this.handleChange}
                            value={this.state.value}/>
        </Panel>
        : null
    );
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    canBeControlled: canBeControlled(fromTravelState(state, ownProps.characterId)),
    movementAction: parseHtmlToComponents(ownProps.characterId,
      getMovementAction(fromTravelState(state, ownProps.characterId))),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    onSubmitDirection: direction => {
      dispatch(changeMovementDirection(ownProps.characterId, direction));
    },
    onSubmitStop: () => {
      dispatch(stopMovement(ownProps.characterId));
    },
    requestState: () => {
      dispatch(requestTravelState(ownProps.characterId));
    },
  }
};

const ControlMovementContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ControlMovement);

export default ControlMovementContainer;
