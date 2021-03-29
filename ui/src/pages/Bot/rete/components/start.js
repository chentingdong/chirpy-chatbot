import Rete from 'rete'
import { strSocket } from '../sockets.js'
// import {getControl} from '../controls/get-control'
import InputControl from '../controls/input'

class ReteStart extends Rete.Component {
  constructor () {
    super('Start')
  }

  builder (node) {
    const input = new Rete.Input('input', 'String', strSocket, true)
    const output = new Rete.Output('output', 'String', strSocket, true)
    return node.addInput(input)
      .addControl(new InputControl('start', this.editor, ''))
      .addOutput(output)
  }
}

export default ReteStart
