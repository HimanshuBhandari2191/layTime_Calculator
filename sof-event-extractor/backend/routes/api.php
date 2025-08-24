use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::post('/upload', function (Request $request) {
    if ($request->hasFile('file')) {
        $path = $request->file('file')->store('uploads', 'public');
        return response()->json(['message' => 'File uploaded successfully', 'path' => $path]);
    }
    return response()->json(['error' => 'No file uploaded'], 400);
});
