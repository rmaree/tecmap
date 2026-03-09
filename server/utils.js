function timestampToDate(timestamp) {
       //const d = new Date(timestamp * 1000);
       const d = new Date(timestamp*1000);
       return d.toLocaleString('fr-BE', {
	   day: '2-digit', month: '2-digit',
	   hour: '2-digit', minute: '2-digit',
	   year: 'numeric'
       });
       
}


module.exports = {
    timestampToDate,
};
