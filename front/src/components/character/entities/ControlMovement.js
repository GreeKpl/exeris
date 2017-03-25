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

class ControlMovement extends React.Component {

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

export default ControlMovement;
