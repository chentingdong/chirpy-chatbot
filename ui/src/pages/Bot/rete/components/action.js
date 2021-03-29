import Rete from 'rete'
import { strSocket } from '../sockets.js'
import InputControl from '../controls/input'
import SelectControl from '../controls/select'
import RadioControl from '../controls/radio'

class ReteAction extends Rete.Component {
  constructor () {
    super('Action')
  }

  builder (node) {
    var input = new Rete.Input('input', 'String', strSocket, true)
    var output = new Rete.Output('output', 'String', strSocket, true)
    var controls = {
      'name': new InputControl('name', this.editor, 'action'),
      'question': new InputControl('question', this.editor, 'question'),
      'context_var': new InputControl('context_var', this.editor, 'context variable'),
      'context_var_mode': new RadioControl('context_var_mode', this.editor, ''),
      'transition': new InputControl('transition', this.editor, 'transition'),
      'action': new SelectControl('action', this.editor, 'action'),
      'template': new InputControl('template', this.editor, 'template')
    }

    node.addInput(input).addOutput(output)
    for (var key in controls) {
      node.addControl(controls[key])
    }
    return node
  }
}

export default ReteAction
