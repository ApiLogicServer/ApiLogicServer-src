import { DataProvider } from 'react-admin'
import { getAppId } from '../../Config';

const handleAIQuery = async (dataProvider: DataProvider, prompt: string) => {
    
    const data = {current : { data: {
        prompt: prompt, 
        name: 'new prompt',
        project_id: getAppId(),
    }}}
    console.log('SPAComponentData:', data);
    try {
        const result = await dataProvider.create('SPAComponent', {
            data: data
        })
        .then((response) => {
            console.log(`Component created with ID: ${response}`);
            document.location.reload();
            return response;
        })
        .catch((error) => {
            console.error('DataProvider error', error);
            alert('DataProvider error');
        })
        
    } catch (error) {
        console.error(`Error: ${error}`);
        alert(`Error: `);
    }
}

export default handleAIQuery;